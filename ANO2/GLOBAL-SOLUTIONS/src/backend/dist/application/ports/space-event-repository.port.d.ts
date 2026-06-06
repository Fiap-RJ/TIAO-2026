import { SpaceEvent } from '../../domain/entities/space-event.entity';
export interface SpaceEventRepositoryPort {
    findAll(): Promise<SpaceEvent[]>;
}
