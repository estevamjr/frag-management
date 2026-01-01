import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import { HttpModule } from '@nestjs/axios'; 
import * as Joi from 'joi';
import { GatewayController } from './gateway.controller';
import { AuthModule } from './auth/auth.module';

@Module({
  imports: [
    // 1. Configuração Blindada
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '../.env'], // Procura na raiz
      validationSchema: Joi.object({
        NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
        PORT: Joi.number().default(8080),
        BACKEND_URL: Joi.string().required(),
        LOG_URL: Joi.string().required(),
        JWT_SECRET: Joi.string().required().min(12),
        JWT_EXPIRATION: Joi.string().default('3600s'),
      }),
    }),

    // 2. Proteção Anti-DDoS
    ThrottlerModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => [{
        ttl: 60000,
        limit: 100,
      }],
    }),

    // 3. Módulo HTTP (Essencial para falar com o Python)
    HttpModule,

    AuthModule, 
  ],
  controllers: [GatewayController],
  providers: [
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}