import { Controller, Get } from '@nestjs/common';
import { FileSpaceEventRepository } from '../../infrastructure/repositories/file-space-event.repository';

@Controller('api/events')
export class EventsController {
  constructor(private readonly repository: FileSpaceEventRepository) {}

  @Get()
  async findAll() {
    const events = await this.repository.findAll();
    return events.map((e) => ({
      id_evento: e.idEvento,
      tipo: e.tipo,
      nome: e.nome,
      data_aproximacao: e.dataAproximacao,
      distancia_terra_km: e.distanciaTerraKm,
      risco_colisao: e.riscoColisao,
      resumo_alerta: e.resumoAlerta,
    }));
  }
}
