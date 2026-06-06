import { ChatAgentPort } from '../../application/ports/chat-agent.port';
import { ChatResponse } from '../../application/dtos/chat.dto';
export declare class LangGraphAgentService implements ChatAgentPort {
    process(message: string): Promise<ChatResponse>;
}
