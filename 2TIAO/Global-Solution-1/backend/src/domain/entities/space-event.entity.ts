export class SpaceEvent {
  constructor(
    public readonly idEvento: string,
    public readonly tipo: string,
    public readonly nome: string,
    public readonly dataAproximacao: string,
    public readonly distanciaTerraKm: number,
    public readonly riscoColisao: boolean,
    public readonly resumoAlerta: string,
  ) {}
}
