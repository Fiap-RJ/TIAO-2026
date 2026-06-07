import { ChatResponse } from '../dtos/chat.dto';

export interface ChatAgentPort {
  process(message: string): Promise<ChatResponse>;
}
