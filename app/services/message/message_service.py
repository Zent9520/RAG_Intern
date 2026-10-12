from backend.app.repositories.chat.message_repository import (

 MessageRepository

)


class MessageService:


 @staticmethod

 async def create(

  db,

  payload

 ):

  return await (

   MessageRepository

   .create(

    db,

    payload

   )

  )