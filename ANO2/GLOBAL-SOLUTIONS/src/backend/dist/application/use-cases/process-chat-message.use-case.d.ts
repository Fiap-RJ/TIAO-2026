import { ChatRequest, ChatResponse } from '../dtos/chat.dto';
import { ChatAgentPort } from '../ports/chat-agent.port';
export declare class ProcessChatMessageUseCase {
    private readonly agent;
    constructor(agent: ChatAgentPort);
    execute(request: ChatRequest): Promise<ChatResponse>;
}
