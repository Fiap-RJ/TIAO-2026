export interface ChatRequest {
    message: string;
}
export interface ChatResponse {
    reply: string;
    source_data: string[];
}
