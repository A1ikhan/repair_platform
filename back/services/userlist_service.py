from back.models import RepairRequest, Response
from back.models.userlist_model import UserList, ListItem
from ninja.errors import HttpError

class UserListService:
    @staticmethod
    def get_or_create_user_lists(user):
        """Создает стандартные списки для пользователя если их нет"""
        lists_created = []
        for list_type, display_name in UserList.LIST_TYPES:
            user_list, created = UserList.objects.get_or_create(
                user=user,
                name=list_type,
                defaults={'name': list_type}
            )
            if created:
                lists_created.append(user_list)
        return lists_created

    @staticmethod
    def get_user_lists(user):
        UserListService.get_or_create_user_lists(user)
        """Получить все списки пользователя"""
        return UserList.objects.filter(user=user).prefetch_related('items')

    @staticmethod
    def get_list_by_name(user, list_name: str):
        """Получить конкретный список по имени"""
        try:
            return UserList.objects.get(user=user, name=list_name)
        except UserList.DoesNotExist:
            raise HttpError(404, f"List '{list_name}' not found")

    @staticmethod
    def add_to_list(user, list_name: str, repair_request_id: int, notes: str = None):
        """Добавить заявку в список"""
        try:
            user_list = UserListService.get_list_by_name(user, list_name)
            repair_request = RepairRequest.objects.get(id=repair_request_id)

            # Проверяем, не добавлена ли уже заявка
            if ListItem.objects.filter(user_list=user_list, repair_request=repair_request).exists():
                raise HttpError(400, "Request already in this list")

            list_item = ListItem.objects.create(
                user_list=user_list,
                repair_request=repair_request,
                notes=notes or ''
            )

            return list_item

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def remove_from_list(user, list_name: str, repair_request_id: int):
        """Удалить заявку из списка"""
        try:
            user_list = UserListService.get_list_by_name(user, list_name)
            list_item = ListItem.objects.get(
                user_list=user_list,
                repair_request_id=repair_request_id
            )
            list_item.delete()
            return {"message": "Item removed from list"}

        except ListItem.DoesNotExist:
            raise HttpError(404, "Item not found in list")

    @staticmethod
    def get_list_items(user, list_name: str):
        UserListService.get_or_create_user_lists(user)
        """Получить элементы списка с пагинацией"""
        user_list = UserListService.get_list_by_name(user, list_name)
        queryset = ListItem.objects.filter(
            user_list=user_list
        ).select_related('repair_request', 'repair_request__created_by')

        return queryset

    @staticmethod
    def update_list_item_notes(user, list_name: str, repair_request_id: int, notes: str):
        """Обновить заметки для элемента списка"""
        try:
            user_list = UserListService.get_list_by_name(user, list_name)
            list_item = ListItem.objects.get(
                user_list=user_list,
                repair_request_id=repair_request_id
            )
            list_item.notes = notes
            list_item.save()
            return list_item

        except ListItem.DoesNotExist:
            raise HttpError(404, "Item not found in list")

    @staticmethod
    def is_in_list(user, repair_request_id: int, list_name: str = None):
        """Проверить, находится ли заявка в списке/списках пользователя"""
        try:
            if list_name:
                # Проверка конкретного списка
                user_list = UserListService.get_list_by_name(user, list_name)
                return ListItem.objects.filter(
                    user_list=user_list,
                    repair_request_id=repair_request_id
                ).exists()
            else:
                # Проверка всех списков
                return ListItem.objects.filter(
                    user_list__user=user,
                    repair_request_id=repair_request_id
                ).exists()

        except RepairRequest.DoesNotExist:
            raise HttpError(404, "Repair request not found")

    @staticmethod
    def get_user_favorites(user):
        """Получить избранные заявки пользователя"""
        return UserListService.get_list_items(user, 'favorite')

    @staticmethod
    def move_between_lists(user, repair_request_id: int, from_list: str, to_list: str):
        """Переместить заявку между списками"""
        try:
            # Удаляем из исходного списка
            UserListService.remove_from_list(user, from_list, repair_request_id)
            # Добавляем в целевой список
            return UserListService.add_to_list(user, to_list, repair_request_id)

        except HttpError as e:
            if "Item not found" in str(e):
                raise HttpError(404, f"Item not found in list '{from_list}'")
            raise e


class AutoListService:
    """Автоматическое управление списками на основе действий пользователя"""

    @staticmethod
    def handle_response_created(response):
        """При создании отклика добавляем заявку в 'Смотрю'"""
        try:
            UserListService.add_to_list(
                response.worker,
                'watching',
                response.repair_request.id,
                notes='Автоматически добавлено при отклике'
            )
        except HttpError:
            pass  # Уже в списке - игнорируем

    @staticmethod
    def handle_response_accepted(response):
        """При принятии отклика перемещаем в 'Подался'"""
        try:
            UserListService.move_between_lists(
                response.worker,
                response.repair_request.id,
                'watching',
                'applied'
            )
        except HttpError:
            pass

    @staticmethod
    def handle_request_completed(repair_request):
        """При завершении заявки перемещаем в 'Выполнено'"""
        try:
            accepted_response = Response.objects.get(
                repair_request=repair_request,
                status='accepted'
            )
            UserListService.move_between_lists(
                accepted_response.worker,
                repair_request.id,
                'applied',
                'completed'
            )
        except (Response.DoesNotExist, HttpError):
            pass