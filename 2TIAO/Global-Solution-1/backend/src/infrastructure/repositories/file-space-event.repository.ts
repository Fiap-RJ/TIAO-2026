import { Injectable, Logger } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import { SpaceEventRepositoryPort } from '../../application/ports/space-event-repository.port';
import { SpaceEvent } from '../../domain/entities/space-event.entity';

@Injectable()
export class FileSpaceEventRepository implements SpaceEventRepositoryPort {
  private readonly filePath = path.join(process.cwd(), 'context_data.json');
  private readonly logger = new Logger(FileSpaceEventRepository.name);

  async findAll(): Promise<SpaceEvent[]> {
    if (!fs.existsSync(this.filePath)) {
      this.logger.warn(`Arquivo de contexto não encontrado em: ${this.filePath}`);
      return [];
    }

    const data = fs.readFileSync(this.filePath, 'utf-8');
    
    try {
      const parsedData = JSON.parse(data);
      
      return parsedData.map((item: any) => new SpaceEvent(
        item.id_evento,
        item.tipo,
        item.nome,
        item.data_aproximacao,
        item.distancia_terra_km,
        item.risco_colisao,
        item.resumo_alerta
      ));
    } catch (error) {
      this.logger.error('Erro ao fazer parse do context_data.json. O arquivo pode estar corrompido.', error);
      return [];
    }
  }
}