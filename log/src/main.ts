import 'tsconfig-paths/register'; // Adicione esta linha no topo!

import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Configuração do Swagger para o Log API
  const config = new DocumentBuilder()
    .setTitle('Log Processing API')
    .setDescription(
      'API responsável por receber, processar e fornecer dados de logs de partidas.',
    )
    .setVersion('1.0')
    .addTag('Logs', 'Endpoints para manipulação de logs')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document); // A rota será http://localhost:3000/api

  await app.listen(3000);
}
bootstrap();
