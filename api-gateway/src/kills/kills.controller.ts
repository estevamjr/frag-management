import { Controller, Get, Req, Res, Param } from '@nestjs/common';
import { ApiTags, ApiBearerAuth } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import type { Request, Response } from 'express';
import { firstValueFrom } from 'rxjs';

@ApiTags('Gateway - Kills')
@ApiBearerAuth()
@Controller('api/v1/kills')
export class KillsController {
  private readonly fragApiUrl: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.fragApiUrl = this.configService.get<string>('FRAG_API_URL') ?? '';
  }

  @Get()
  async getAll(@Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.get(`${this.fragApiUrl}/kills`, { 
          params: req.query,
          headers: { Authorization: req.headers['authorization'] || '' }
        }),
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @Get(':id')
  async getById(@Param('id') id: string, @Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.get(`${this.fragApiUrl}/kills/${id}`, { 
          headers: { Authorization: req.headers['authorization'] || '' }
        })
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }
}