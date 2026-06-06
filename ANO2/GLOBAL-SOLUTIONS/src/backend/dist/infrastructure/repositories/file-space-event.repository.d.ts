import { SpaceEventRepositoryPort } from '../../application/ports/space-event-repository.port';
import { SpaceEvent } from '../../domain/entities/space-event.entity';
export declare class FileSpaceEventRepository implements SpaceEventRepositoryPort {
    private readonly filePath;
    findAll(): Promise<SpaceEvent[]>;
}
