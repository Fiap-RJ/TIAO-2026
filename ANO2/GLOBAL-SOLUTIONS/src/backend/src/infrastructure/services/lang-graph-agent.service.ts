import { Injectable } from '@nestjs/common';
import { ChatAgentPort } from '../../application/ports/chat-agent.port';
import { ChatResponse } from '../../application/dtos/chat.dto';

@Injectable()
export class LangGraphAgentService implements ChatAgentPort {
  async process(message: string): Promise<ChatResponse> {
    // Mocked response for now
    return {
      reply: `Agente processou: ${message}`,
      source_data: ["Mock Data 1"]
    };
  }
}
