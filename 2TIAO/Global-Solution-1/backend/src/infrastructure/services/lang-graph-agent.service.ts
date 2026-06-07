import { Injectable, Logger } from '@nestjs/common';
import { StateGraph, END, START, Annotation } from '@langchain/langgraph';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { ChatAgentPort } from '../../application/ports/chat-agent.port';
import { ChatResponse } from '../../application/dtos/chat.dto';
import { FileSpaceEventRepository } from '../repositories/file-space-event.repository';

// Define the state schema using Annotation
const AgentState = Annotation.Root({
  query: Annotation<string>,
  context: Annotation<string>,
  reply: Annotation<string>,
  source_data: Annotation<string[]>,
  validationPassed: Annotation<boolean>,
});

@Injectable()
export class LangGraphAgentService implements ChatAgentPort {
  private graph: any;
  private model: ChatGoogleGenerativeAI;
  private readonly logger = new Logger(LangGraphAgentService.name);

  constructor(private readonly fileSpaceEventRepository: FileSpaceEventRepository) {
    this.model = new ChatGoogleGenerativeAI({
      apiKey: process.env.GOOGLE_API_KEY,
      model: 'gemini-3.1-flash-lite-preview',
      temperature: 0.7,
    });
    this.graph = this.buildGraph();
  }

  private buildGraph() {
    const workflow = new StateGraph(AgentState)
      .addNode('retrieveData', this.retrieveData.bind(this))
      .addNode('generateResponse', this.generateResponse.bind(this))
      .addNode('validator', this.validator.bind(this))
      .addEdge(START, 'retrieveData')
      .addEdge('retrieveData', 'generateResponse')
      .addEdge('generateResponse', 'validator')
      .addConditionalEdges(
        'validator',
        (state) => (state.validationPassed ? END : 'retrieveData')
      );

    return workflow.compile();
  }

  private async retrieveData(state: typeof AgentState.State): Promise<Partial<typeof AgentState.State>> {
    const start = Date.now();
    this.logger.log('Entering retrieveData node');
    try {
      const events = await this.fileSpaceEventRepository.findAll();
      
      const context = events
        .map((e) => `${e.nome} (Risco: ${e.riscoColisao ? 'Sim' : 'Não'})`)
        .join('\n');
      
      const source_data = events.map(
        (e) => `${e.nome} - Risco: ${e.riscoColisao}`,
      );
      
      this.logger.log(`Exiting retrieveData node. Took ${Date.now() - start}ms`);
      return { context, source_data };
    } catch (error) {
      this.logger.error('Error in retrieveData node', error);
      return { context: 'No context available.', source_data: [] };
    }
  }

  private async generateResponse(state: typeof AgentState.State): Promise<Partial<typeof AgentState.State>> {
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

  private async validator(state: typeof AgentState.State): Promise<Partial<typeof AgentState.State>> {
    const start = Date.now();
    this.logger.log('Entering validator node');
    
    const hasContent = !!state.reply && state.reply.length > 10;
    const hasContextReference = state.context.split('\n').some(line => state.reply.includes(line.split(' ')[0]));
    
    const passed: boolean = !!(hasContent && hasContextReference);

    if (!passed) {
      this.logger.warn(`Validation failed. Content: ${hasContent}, ContextRef: ${hasContextReference}`);
    }

    this.logger.log(`Exiting validator node. Took ${Date.now() - start}ms`);
    return { validationPassed: passed };
  }

  async process(message: string): Promise<ChatResponse> {
    const initialState = { 
      query: message, 
      context: '', 
      reply: '', 
      source_data: [], 
      validationPassed: false 
    };
    
    const result = await this.graph.invoke(initialState);
    return {
      reply: result.reply,
      source_data: result.source_data
    };
  }
}
