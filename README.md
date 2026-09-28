# Pautas Shorts Research

Ferramenta local de pesquisa editorial para vídeos curtos sobre histórias humanas,
fenômenos naturais, geologia, arqueologia, espaço e ciência.

## Estado do projeto

A integração com Reddit está **desativada até que o operador receba aprovação
formal do Reddit e credenciais OAuth autorizadas**. Nenhuma chave é incluída
neste repositório.

O componente previsto é estritamente de leitura. Ele consulta listagens
públicas recentes de:

- r/volcanoes
- r/geology
- r/archaeology
- r/space

A coleta é limitada a 25 posts por comunidade e usa apenas título, data,
pontuação agregada, total agregado de comentários e link. Não lê comentários,
perfis, mensagens privadas ou dados sensíveis; não publica, vota, comenta ou
envia mensagens.

## Fluxo editorial

1. O operador inicia a pesquisa manualmente no Windows.
2. Sinais agregados do Reddit sugerem um possível tema.
3. O fato é confirmado em fontes jornalísticas ou oficiais independentes.
4. O roteiro diferencia evidência confirmada, hipótese e informação ainda
   desconhecida.
5. Um tema só vira vídeo se respeitar as regras editoriais e de segurança.

Leia [PRIVACY.md](PRIVACY.md) para os limites de dados. As credenciais, quando
aprovadas, devem ficar somente em configuração local ignorada pelo Git.

