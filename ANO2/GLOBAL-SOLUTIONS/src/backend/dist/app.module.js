"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppModule = void 0;
const common_1 = require("@nestjs/common");
const chat_controller_1 = require("./presentation/controllers/chat.controller");
const process_chat_message_use_case_1 = require("./application/use-cases/process-chat-message.use-case");
const lang_graph_agent_service_1 = require("./infrastructure/services/lang-graph-agent.service");
const file_space_event_repository_1 = require("./infrastructure/repositories/file-space-event.repository");
let AppModule = class AppModule {
};
exports.AppModule = AppModule;
exports.AppModule = AppModule = __decorate([
    (0, common_1.Module)({
        imports: [],
        controllers: [chat_controller_1.ChatController],
        providers: [
            file_space_event_repository_1.FileSpaceEventRepository,
            lang_graph_agent_service_1.LangGraphAgentService,
            {
                provide: process_chat_message_use_case_1.ProcessChatMessageUseCase,
                useFactory: (agentService) => {
                    return new process_chat_message_use_case_1.ProcessChatMessageUseCase(agentService);
                },
                inject: [lang_graph_agent_service_1.LangGraphAgentService],
            },
        ],
    })
], AppModule);
//# sourceMappingURL=app.module.js.map