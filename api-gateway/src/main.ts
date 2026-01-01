import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common'; // <--- Importante para a segurança
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // --- 1. BLINDAGEM DE SEGURANÇA (O Guardião) ---
  // Isso ativa as regras que definimos no DTO (whitelisting, transform)
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,            // Remove chaves que não estão no DTO (limpa o lixo)
    forbidNonWhitelisted: true, // Dá erro se mandar chaves extras (alerta de ataque)
    transform: true,            // Converte tipos automaticamente
  }));

  // --- 2. CONFIGURAÇÃO DO SWAGGER (Documentação) ---
  const config = new DocumentBuilder()
    .setTitle('Frag Management - API Gateway')
    .setDescription(
      'Ponto de entrada único para todos os microsserviços do sistema de gerenciamento de frags.',
    )
    .setVersion('1.0')
    .addBearerAuth() // Adiciona o botão de "Authorize" (cadeado) para testar login depois
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api-docs', app, document); // A rota será http://localhost:8080/api-docs

  // --- 3. HABILITA CORS ---
  // Essencial para o Frontend (React) conseguir falar com essa API
  app.enableCors();

  await app.listen(8080);
}
bootstrap();