from apps.chat.typesd.request.base import BaseRecord, BaseMessage


class RecallRecordItem(BaseMessage):
    pass


class RecallRecord(BaseRecord):
    message: RecallRecordItem
