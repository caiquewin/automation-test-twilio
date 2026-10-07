# automation-test-twilio

Projeto de automação para **enviar e receber mensagens no WhatsApp**.

## Como funciona

Em vez da API oficial do WhatsApp Business (ou de um provedor como a Twilio), o projeto usa uma **biblioteca da comunidade** que se conecta ao WhatsApp da mesma forma que o **WhatsApp Web**:

1. Ao iniciar, a aplicação gera um **QR Code** no terminal.
2. No celular, abra o WhatsApp → **Aparelhos conectados** → **Conectar um aparelho** e escaneie o QR Code.
3. A sessão fica salva localmente, então não é preciso escanear de novo a cada execução (a menos que a sessão expire ou seja desconectada pelo celular).
4. Com a sessão ativa, a aplicação consegue:
   - **enviar** mensagens para um número ou grupo;
   - **receber** mensagens por meio de eventos/listeners e reagir a elas (por exemplo, respostas automáticas).

## Biblioteca

> A definir. Opções comuns da comunidade:
> - [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) (Node.js, usa um navegador headless via Puppeteer)
> - [Baileys](https://github.com/WhiskeySockets/Baileys) (Node.js, conecta direto pelo protocolo WebSocket, sem navegador)

## Avisos importantes

- Essas bibliotecas **não são oficiais** e não têm vínculo com o WhatsApp/Meta. Usar clientes não oficiais pode violar os Termos de Serviço do WhatsApp e levar ao **banimento do número**. Prefira usar um número de testes.
- Os dados de sessão salvos localmente dão acesso total à conta do WhatsApp conectada. **Não faça commit deles** (adicione a pasta de sessão ao `.gitignore`).
- Atualizações do WhatsApp Web podem quebrar a biblioteca temporariamente. Mantenha a dependência atualizada.

## Instalação e uso

_Em construção. Esta seção será preenchida quando a biblioteca e a estrutura do projeto forem definidas._
