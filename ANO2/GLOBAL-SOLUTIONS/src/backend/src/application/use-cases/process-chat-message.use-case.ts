import { ChatRequest, ChatResponse } from '../dtos/chat.dto';

export class ProcessChatMessageUseCase {
  async execute(request: ChatRequest): Promise<ChatResponse> {
    // Mocked response based on the contract
    return {
      reply: "Atualmente, o asteroide Apophis está sendo monitorado...",
      source_data: ["Apophis - Risco: true"]
    };
  }
}
