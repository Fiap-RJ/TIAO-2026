import { Controller, Post, Body } from '@nestjs/common';
import { ProcessChatMessageUseCase } from '../../application/use-cases/process-chat-message.use-case';
import { ChatRequest, ChatResponse } from '../../application/dtos/chat.dto';

@Controller('api/chat')
export class ChatController {
  constructor(private readonly processChatMessageUseCase: ProcessChatMessageUseCase) {}

  @Post()
  async handle(@Body() request: ChatRequest): Promise<ChatResponse> {
    return await this.processChatMessageUseCase.execute(request);
  }
}
