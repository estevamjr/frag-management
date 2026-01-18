import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import { HttpModule } from '@nestjs/axios'; 
import * as Joi from 'joi';

import { AuthModule } from './auth/auth.module';
import { MatchesController } from './matches/matches.controller';
import { PlayersController } from './players/players.controller';
import { LogsController } from './logs/logs.controller';
import { KillsController } from './kills/kills.controller'; // <--- NOVO
import { TasksController } from './tasks/tasks.controller'; // <--- NOVO

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '../.env'],
      validationSchema: Joi.object({
        NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
        PORT: Joi.number().default(8080),
        FRAG_API_URL: Joi.string().required(),
        LOG_API_URL: Joi.string().required(),
        JWT_SECRET: Joi.string().required().min(12),
        JWT_EXPIRATION: Joi.string().default('3600s'),
        HTTP_TIMEOUT: Joi.number().default(5000),
      }),
    }),
    ThrottlerModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => [{ ttl: 60000, limit: 100 }],
    }),
    HttpModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        timeout: configService.get<number>('HTTP_TIMEOUT'),
        maxRedirects: 5,
      }),
      inject: [ConfigService],
    }),
    AuthModule,
  ],
  controllers: [
    MatchesController,
    PlayersController,
    LogsController,
    KillsController, // <--- REGISTRADO
    TasksController, // <--- REGISTRADO
  ],
  providers: [
    { provide: APP_GUARD, useClass: ThrottlerGuard },
  ],
})
export class AppModule {}