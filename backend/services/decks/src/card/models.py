from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict


class SCardCreate(BaseModel):
    front_text: str
    front_image_url: Optional[str] = None
    back_text: str
    back_image_url: Optional[str] = None
    order_index: Optional[int] = 0


class SCardUpdate(BaseModel):
    front_text: Optional[str] = None
    front_image_url: Optional[str] = None
    back_text: Optional[str] = None
    back_image_url: Optional[str] = None
    order_index: Optional[int] = None


class SCardResponse(BaseModel):
    id: int
    deck_id: int
    front_text: str
    front_image_url: Optional[str] = None
    back_text: str
    back_image_url: Optional[str] = None
    order_index: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class SCardBulkItem(BaseModel):
    """Элемент для bulk-операций над карточками.

    - Если указан id и присутствуют поля карточки → обновление существующей карточки.
    - Если id не указан → создание новой карточки.
    - Если to_delete == true и указан id → удаление карточки с этим id (остальные поля игнорируются).
    - Поля, не переданные при обновлении, остаются без изменений.
    """

    id: Optional[int] = None
    front_text: Optional[str] = None
    front_image_url: Optional[str] = None
    back_text: Optional[str] = None
    back_image_url: Optional[str] = None
    order_index: Optional[int] = None
    to_delete: Optional[bool] = False

    model_config = ConfigDict(extra="forbid")


class SPresignUploadRequest(BaseModel):
    filename: str  # имя файла (чтобы получить расширение)


class SPresignUploadResponse(BaseModel):
    put_url: str
    get_url: str
    object_key: str  # ссылка на файл в хранилище
