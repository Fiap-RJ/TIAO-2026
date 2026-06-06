"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProcessChatMessageUseCase = void 0;
class ProcessChatMessageUseCase {
    constructor(agent) {
        this.agent = agent;
    }
    async execute(request) {
        return await this.agent.process(request.message);
    }
}
exports.ProcessChatMessageUseCase = ProcessChatMessageUseCase;
//# sourceMappingURL=process-chat-message.use-case.js.map