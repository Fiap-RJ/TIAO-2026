import { ProcessChatMessageUseCase } from '../../application/use-cases/process-chat-message.use-case';
import { ChatRequest, ChatResponse } from '../../application/dtos/chat.dto';
export declare class ChatController {
    private readonly processChatMessageUseCase;
    constructor(processChatMessageUseCase: ProcessChatMessageUseCase);
    handle(request: ChatRequest): Promise<ChatResponse>;
}
