export declare class SpaceEvent {
    readonly idEvento: string;
    readonly tipo: string;
    readonly nome: string;
    readonly dataAproximacao: string;
    readonly distanciaTerraKm: number;
    readonly riscoColisao: boolean;
    readonly resumoAlerta: string;
    constructor(idEvento: string, tipo: string, nome: string, dataAproximacao: string, distanciaTerraKm: number, riscoColisao: boolean, resumoAlerta: string);
}
