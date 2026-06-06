import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import { SpaceEventRepositoryPort } from '../../application/ports/space-event-repository.port';
import { SpaceEvent } from '../../domain/entities/space-event.entity';

@Injectable()
export class FileSpaceEventRepository implements SpaceEventRepositoryPort {
  private readonly filePath = path.join(process.cwd(), 'context_data.json');

  async findAll(): Promise<SpaceEvent[]> {
    if (!fs.existsSync(this.filePath)) {
      return [];
    }
    const data = fs.readFileSync(this.filePath, 'utf-8');
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
  }
}
