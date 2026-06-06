import { ChatRequest, ChatResponse } from '../dtos/chat.dto';
import { ChatAgentPort } from '../ports/chat-agent.port';

export class ProcessChatMessageUseCase {
  constructor(private readonly agent: ChatAgentPort) {}

  async execute(request: ChatRequest): Promise<ChatResponse> {
    return await this.agent.process(request.message);
  }
}
