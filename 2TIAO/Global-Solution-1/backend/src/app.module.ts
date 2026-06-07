import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ChatController } from './presentation/controllers/chat.controller';
import { EventsController } from './presentation/controllers/events.controller';
import { ProcessChatMessageUseCase } from './application/use-cases/process-chat-message.use-case';
import { LangGraphAgentService } from './infrastructure/services/lang-graph-agent.service';
import { FileSpaceEventRepository } from './infrastructure/repositories/file-space-event.repository';

@Module({
  imports: [ConfigModule.forRoot()],
  controllers: [ChatController, EventsController],
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
