import { Module } from '@nestjs/common';
import { ChatController } from './presentation/controllers/chat.controller';
import { ProcessChatMessageUseCase } from './application/use-cases/process-chat-message.use-case';
import { LangGraphAgentService } from './infrastructure/services/lang-graph-agent.service';
import { FileSpaceEventRepository } from './infrastructure/repositories/file-space-event.repository';

@Module({
  imports: [],
  controllers: [ChatController],
  providers: [
    FileSpaceEventRepository,
    LangGraphAgentService,
    {
      provide: ProcessChatMessageUseCase,
      useFactory: (agentService: LangGraphAgentService) => {
        return new ProcessChatMessageUseCase(agentService);
      },
      inject: [LangGraphAgentService],
    },
  ],
})
export class AppModule {}
