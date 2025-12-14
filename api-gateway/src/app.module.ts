import { Module } from '@nestjs/common';
import { GatewayController } from './gateway.controller'; // Importa o controlador correto
import { HttpModule } from '@nestjs/axios';

@Module({
  imports: [
    HttpModule.register({
      timeout: 5000,
      maxRedirects: 5,
    }),
  ],
  controllers: [GatewayController], // Usa o GatewayController
})
export class AppModule {}
