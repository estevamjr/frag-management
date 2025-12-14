import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Configuração do Swagger
  const config = new DocumentBuilder()
    .setTitle('Frag Management - API Gateway')
    .setDescription(
      'Ponto de entrada único para todos os microsserviços do sistema de gerenciamento de frags.',
    )
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api-docs', app, document); // A rota será http://localhost:8080/api-docs

  await app.listen(8080);
}
bootstrap();
