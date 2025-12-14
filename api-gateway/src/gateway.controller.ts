import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  // All,
  Req,
  Res,
  Param,
  Body,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { HttpService } from '@nestjs/axios';
import type { Request, Response } from 'express';
import 'multer'; // Import para disponibilizar os tipos do Multer globalmente
import { firstValueFrom } from 'rxjs';
import { FileInterceptor } from '@nestjs/platform-express';
import FormData from 'form-data';
// import { Stream } from 'stream';

@Controller('api/v1') // Nosso prefixo global da API
export class GatewayController {
  // URLs dos nossos serviços internos (usando DNS do Docker)
  private readonly fragApiUrl = 'http://frag-api:8000/api/v1';
  private readonly logApiUrl = 'http://log-api:3000/logs';

  constructor(private readonly httpService: HttpService) {}

  // --- ROTAS DO FRAG-API (Python/FastAPI) ---

  // --- Matches ---
  @ApiTags('Gateway - Matches')
  @Get('/matches')
  async proxyMatches(@Req() req: Request, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/matches`;
      const { data } = await firstValueFrom(
        this.httpService.get(url, { params: req.query }),
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Matches')
  @Get('/matches/:id')
  async proxyMatchById(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/matches/${id}`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Matches')
  @Put('/matches/:id')
  async updateMatch(
    @Param('id') id: string,
    @Body() body: any,
    @Res() res: Response,
  ) {
    try {
      const url = `${this.fragApiUrl}/matches/${id}`;
      const { data } = await firstValueFrom(this.httpService.put(url, body));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Matches')
  @Delete('/matches/:id')
  async deleteMatch(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/matches/${id}`;
      const { data } = await firstValueFrom(this.httpService.delete(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- Players ---
  @ApiTags('Gateway - Players')
  @Get('/players')
  async proxyPlayers(@Req() req: Request, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/players`;
      const { data } = await firstValueFrom(
        this.httpService.get(url, { params: req.query }),
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Players')
  @Get('/players/:id')
  async proxyPlayerById(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/players/${id}`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- Kills ---
  @ApiTags('Gateway - Kills')
  @Get('/kills')
  async proxyKills(@Req() req: Request, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/kills`;
      const { data } = await firstValueFrom(
        this.httpService.get(url, { params: req.query }),
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Kills')
  @Get('/kills/:id')
  async proxyKillById(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/kills/${id}`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- Tasks ---
  @ApiTags('Gateway - Frag') // Agrupado com Frag, pois é uma tarefa do frag-api
  @Get('/tasks/status/:id')
  async getTaskStatus(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.fragApiUrl}/tasks/status/${id}`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- ROTAS DO LOG-API (Node/NestJS) ---
  @ApiTags('Gateway - Ranking')
  @Get('/ranking/global')
  async proxyRanking(@Req() req: Request, @Res() res: Response) {
    try {
      const url = `${this.logApiUrl}/ranking/global`;
      const { data } = await firstValueFrom(
        this.httpService.get(url, { params: req.query }),
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Logs')
  @Post('/logs/upload')
  @UseInterceptors(FileInterceptor('file'))
  async proxyLogUpload(
    @UploadedFile() file: Express.Multer.File,
    @Body() body: any,
    @Res() res: Response,
  ) {
    try {
      const url = `${this.logApiUrl}/upload`;

      const formData = new FormData();
      formData.append('file', file.buffer, file.originalname);

      // Repassa o campo 'teams' se ele existir no corpo da requisição
      if (body.teams) {
        formData.append('teams', body.teams);
      }

      const { data } = await firstValueFrom(
        this.httpService.post(url, formData, {
          headers: {
            ...formData.getHeaders(),
          },
        }),
      );
      res.status(201).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Logs')
  @Get('/logs/matches')
  async proxyLogMatches(@Req() _req: Request, @Res() res: Response) {
    try {
      const url = `${this.logApiUrl}/matches`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Ranking') // Movido para Ranking, pois é um relatório de MVP
  @Get('/logs/matches/mvp')
  async proxyMvpReport(@Req() _req: Request, @Res() res: Response) {
    try {
      const url = `${this.logApiUrl}/matches/mvp`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @ApiTags('Gateway - Logs')
  @Get('/logs/matches/:id')
  async proxyMatchDetails(@Param('id') id: string, @Res() res: Response) {
    try {
      const url = `${this.logApiUrl}/matches/${id}`;
      const { data } = await firstValueFrom(this.httpService.get(url));
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- ROTA DE UPLOAD PARA O FRAG-API ---
  // Rota separada para evitar conflito com o upload do log-api
  @ApiTags('Gateway - Frag')
  @Post('/frag-api/upload')
  @UseInterceptors(FileInterceptor('file'))
  async proxyFragApiUpload(
    @UploadedFile() file: Express.Multer.File,
    @Res() res: Response,
  ) {
    try {
      const url = `${this.fragApiUrl}/matches/upload`;

      const formData = new FormData();
      formData.append('file', file.buffer, file.originalname);

      const { data } = await firstValueFrom(
        this.httpService.post(url, formData, {
          headers: {
            ...formData.getHeaders(),
          },
        }),
      );
      // A API de destino retorna 202 (Accepted)
      res.status(202).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }
}
