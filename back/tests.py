from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from back.models import (
    CustomerProfile, WorkerProfile, RepairRequest, Response, Review,
)
from back.schemas.repair_requests_schema import RepairRequestSchemaIn
from back.schemas.users_schema import UserCreate
from back.services.user_service import UserService
from back.services.response_service import ResponseService
from back.services.repair_request_service import RepairRequestService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_customer(username="customer1"):
    user = User.objects.create_user(username, f"{username}@test.com", "pass1234")
    CustomerProfile.objects.create(user=user)
    return user


def _make_worker(username="worker1"):
    user = User.objects.create_user(username, f"{username}@test.com", "pass1234")
    WorkerProfile.objects.create(user=user)
    return user


def _make_repair_request(customer, title="Fridge broken", device_type="fridge"):
    return RepairRequest.objects.create(
        title=title,
        description="It stopped cooling",
        device_type=device_type,
        address="Test Street 1",
        created_by=customer,
        status="new",
    )


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class SchemaValidationTests(TestCase):
    def test_password_too_short_raises(self):
        with self.assertRaises(Exception):
            UserCreate(
                username="u", email="u@e.com",
                password="short",  # < 8 chars
                user_type="customer",
            )

    def test_invalid_user_type_raises(self):
        with self.assertRaises(Exception):
            UserCreate(
                username="u", email="u@e.com",
                password="valid1234",
                user_type="admin",  # invalid
            )

    def test_invalid_device_type_raises(self):
        with self.assertRaises(Exception):
            RepairRequestSchemaIn(
                title="Test",
                description="Desc",
                device_type="blender",  # invalid
                address="Addr",
            )

    def test_valid_repair_request_schema(self):
        schema = RepairRequestSchemaIn(
            title="Fridge repair",
            description="Not working",
            device_type="fridge",
            address="Some street",
        )
        self.assertEqual(schema.device_type, "fridge")

    def test_valid_user_create_schema(self):
        schema = UserCreate(
            username="validuser",
            email="valid@example.com",
            password="strongpass",
            user_type="worker",
        )
        self.assertEqual(schema.user_type, "worker")


# ---------------------------------------------------------------------------
# UserService tests
# ---------------------------------------------------------------------------

class UserServiceTests(TestCase):
    def test_create_customer(self):
        data = UserCreate(
            username="cust1", email="cust1@test.com",
            password="testpass1", user_type="customer",
        )
        user = UserService.create_user(data, "customer")
        self.assertTrue(hasattr(user, "customer_profile"))
        self.assertFalse(hasattr(user, "worker_profile"))

    def test_create_worker(self):
        data = UserCreate(
            username="work1", email="work1@test.com",
            password="testpass1", user_type="worker",
        )
        user = UserService.create_user(data, "worker")
        self.assertTrue(hasattr(user, "worker_profile"))

    def test_duplicate_username_raises(self):
        data = UserCreate(
            username="dup", email="dup@test.com",
            password="testpass1", user_type="customer",
        )
        UserService.create_user(data, "customer")
        with self.assertRaises(Exception):
            UserService.create_user(data, "customer")

    def test_invalid_user_type_raises(self):
        data = UserCreate(
            username="badtype", email="bad@test.com",
            password="testpass1", user_type="customer",
        )
        data.user_type = "unknown"  # bypass schema validator for service test
        with self.assertRaises(Exception):
            UserService.create_user(data, "unknown")


# ---------------------------------------------------------------------------
# ResponseService — atomicity and permissions
# ---------------------------------------------------------------------------

class ResponseServiceTests(TestCase):
    def setUp(self):
        self.customer = _make_customer("cust_resp")
        self.worker1 = _make_worker("work_resp1")
        self.worker2 = _make_worker("work_resp2")
        self.repair = _make_repair_request(self.customer)

    class _ResponseData:
        def __init__(self, message, proposed_price):
            self.message = message
            self.proposed_price = proposed_price

    def _create_response(self, worker, price=1000):
        data = self._ResponseData("I can fix it", price)
        return ResponseService.create_response(self.repair.id, data, worker)

    def test_accept_response_rejects_others_atomically(self):
        resp1 = self._create_response(self.worker1)
        resp2 = self._create_response(self.worker2)

        ResponseService.accept_response(resp1.id, self.customer)

        resp1.refresh_from_db()
        resp2.refresh_from_db()
        self.repair.refresh_from_db()

        self.assertEqual(resp1.status, "accepted")
        self.assertEqual(resp2.status, "rejected")
        self.assertEqual(self.repair.status, "active")

    def test_non_owner_cannot_accept(self):
        resp = self._create_response(self.worker1)
        other_customer = _make_customer("other_cust")
        from ninja.errors import HttpError
        with self.assertRaises(HttpError) as ctx:
            ResponseService.accept_response(resp.id, other_customer)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_duplicate_response_raises(self):
        self._create_response(self.worker1)
        from ninja.errors import HttpError
        with self.assertRaises(HttpError):
            self._create_response(self.worker1)


# ---------------------------------------------------------------------------
# Model constraint tests
# ---------------------------------------------------------------------------

class ModelConstraintTests(TestCase):
    def setUp(self):
        self.customer = _make_customer("cust_model")
        self.worker = _make_worker("work_model")
        self.repair = _make_repair_request(self.customer)

    def test_review_rating_validator_rejects_zero(self):
        review = Review(
            repair_request=self.repair,
            worker=self.worker,
            customer=self.customer,
            rating=0,
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_rating_validator_rejects_six(self):
        review = Review(
            repair_request=self.repair,
            worker=self.worker,
            customer=self.customer,
            rating=6,
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_response_negative_price_validator(self):
        response = Response(
            repair_request=self.repair,
            worker=self.worker,
            message="hello",
            proposed_price=-100,
            status="sent",
        )
        with self.assertRaises(ValidationError):
            response.full_clean()


# ---------------------------------------------------------------------------
# Public API smoke tests (no auth required)
# ---------------------------------------------------------------------------

class PublicApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        customer = _make_customer("api_cust")
        self.repair = _make_repair_request(customer)

    def test_list_repairs_returns_200(self):
        resp = self.client.get("/api/repairs/")
        self.assertEqual(resp.status_code, 200)

    def test_get_repair_by_id_returns_200(self):
        resp = self.client.get(f"/api/repairs/{self.repair.id}")
        self.assertEqual(resp.status_code, 200)

    def test_search_repairs_returns_200(self):
        resp = self.client.get("/api/repairs/search?search=fridge")
        self.assertEqual(resp.status_code, 200)

    def test_filters_endpoint_returns_200(self):
        resp = self.client.get("/api/repairs/filters")
        self.assertEqual(resp.status_code, 200)

    def test_top_workers_returns_200(self):
        resp = self.client.get("/api/workers/top")
        self.assertEqual(resp.status_code, 200)
