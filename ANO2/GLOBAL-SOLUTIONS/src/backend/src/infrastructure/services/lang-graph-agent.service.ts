import { Injectable, Logger } from '@nestjs/common';
import { StateGraph, END, START } from '@langchain/langgraph';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { ChatAgentPort } from '../../application/ports/chat-agent.port';
import { ChatResponse } from '../../application/dtos/chat.dto';
import { FileSpaceEventRepository } from '../repositories/file-space-event.repository';

interface AgentState {
  query: string;
  context: string;
  reply: string;
  source_data: string[];
  validationPassed: boolean;
}

@Injectable()
export class LangGraphAgentService implements ChatAgentPort {
  private graph: any;
  private model: ChatGoogleGenerativeAI;
  private readonly logger = new Logger(LangGraphAgentService.name);

  constructor(private readonly fileSpaceEventRepository: FileSpaceEventRepository) {
    this.model = new ChatGoogleGenerativeAI({
      apiKey: process.env.GOOGLE_API_KEY,
      modelName: 'gemini-pro',
      temperature: 0.7,
    });
    this.graph = this.buildGraph();
  }

  private buildGraph() {
    const workflow = new StateGraph<AgentState>({
      channels: {
        query: { value: (x: string, y: string) => y, default: () => '' },
        context: { value: (x: string, y: string) => y, default: () => '' },
        reply: { value: (x: string, y: string) => y, default: () => '' },
        source_data: { value: (x: string[], y: string[]) => y, default: () => [] },
        validationPassed: { value: (x: boolean, y: boolean) => y, default: () => false },
      },
    });

    workflow.addNode('retrieveData', this.retrieveData.bind(this));
    workflow.addNode('generateResponse', this.generateResponse.bind(this));
    workflow.addNode('validator', this.validator.bind(this));

    workflow.addEdge(START, 'retrieveData');
    workflow.addEdge('retrieveData', 'generateResponse');
    workflow.addEdge('generateResponse', 'validator');

    workflow.addConditionalEdges(
      'validator',
      (state) => (state.validationPassed ? END : 'retrieveData')
    );

    return workflow.compile();
  }

  private async retrieveData(state: AgentState): Promise<Partial<AgentState>> {
    const start = Date.now();
    this.logger.log('Entering retrieveData node');
    try {
      const events = await this.fileSpaceEventRepository.findAll();
      
      const context = events
        .map((e) => `${e.nome} (Risco: ${e.risco_colisao ? 'Sim' : 'Não'})`)
        .join('\n');
      
      const source_data = events.map(
        (e) => `${e.nome} - Risco: ${e.risco_colisao}`,
      );
      
      this.logger.log(`Exiting retrieveData node. Took ${Date.now() - start}ms`);
      return { context, source_data };
    } catch (error) {
      this.logger.error('Error in retrieveData node', error);
      return { context: 'No context available.', source_data: [] };
    }
  }

  private async generateResponse(state: AgentState): Promise<Partial<AgentState>> {
    const start = Date.now();
    this.logger.log('Entering generateResponse node');
    
    const prompt = `
      You are a space monitoring assistant. Use the following context to answer the user's query.
      Context:
      ${state.context}

      User Query: ${state.query}
    `;

    const response = await this.model.invoke(prompt);
    
    this.logger.log(`Exiting generateResponse node. Took ${Date.now() - start}ms`);
    return { reply: response.content.toString() };
  }

  private async validator(state: AgentState): Promise<Partial<AgentState>> {
    const start = Date.now();
    this.logger.log('Entering validator node');
    
    // Validation logic: check if reply is not empty and contains relevant keywords from context
    const hasContent = state.reply && state.reply.length > 10;
    const hasContextReference = state.context.split('\n').some(line => state.reply.includes(line.split(' ')[0]));
    const passed = hasContent && hasContextReference;

    if (!passed) {
      this.logger.warn(`Validation failed. Content: ${hasContent}, ContextRef: ${hasContextReference}`);
    }

    this.logger.log(`Exiting validator node. Took ${Date.now() - start}ms`);
    return { validationPassed: passed };
  }

  async process(message: string): Promise<ChatResponse> {
    const result = await this.graph.invoke({ query: message });
    return {
      reply: result.reply,
      source_data: result.source_data
    };
  }
}
