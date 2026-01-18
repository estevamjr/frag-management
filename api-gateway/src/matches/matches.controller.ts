import { Controller, Get, Post, Put, Delete, Req, Res, Param, Body, UploadedFile, UseInterceptors } from '@nestjs/common';
import { ApiTags, ApiBearerAuth, ApiBody, ApiConsumes } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import type { Request, Response } from 'express';
import { firstValueFrom } from 'rxjs';
import { FileInterceptor } from '@nestjs/platform-express';
import FormData from 'form-data';

@ApiTags('Gateway - Matches')
@ApiBearerAuth()
@Controller('api/v1/matches')
export class MatchesController {
  private readonly fragApiUrl: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.fragApiUrl = this.configService.get<string>('FRAG_API_URL') ?? '';
  }

  private getHeaders(req: Request) {
    return { Authorization: req.headers['authorization'] || '' };
  }

  @Get()
  async getAll(@Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.get(`${this.fragApiUrl}/matches`, { 
          params: req.query,
          headers: this.getHeaders(req) 
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
        this.httpService.get(`${this.fragApiUrl}/matches/${id}`, { headers: this.getHeaders(req) })
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @Post()
  @ApiBody({ schema: { type: 'object', properties: { match_id: { type: 'string' } } } })
  async create(@Body() body: any, @Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.post(`${this.fragApiUrl}/matches`, body, { headers: this.getHeaders(req) })
      );
      res.status(201).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  // --- ROTAS RESTAURADAS ---
  @Put(':id')
  async update(@Param('id') id: string, @Body() body: any, @Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.put(`${this.fragApiUrl}/matches/${id}`, body, { headers: this.getHeaders(req) })
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }

  @Delete(':id')
  async delete(@Param('id') id: string, @Req() req: Request, @Res() res: Response) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.delete(`${this.fragApiUrl}/matches/${id}`, { headers: this.getHeaders(req) })
      );
      res.status(200).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }
  // -------------------------

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  @ApiConsumes('multipart/form-data')
  @ApiBody({
    schema: { type: 'object', properties: { file: { type: 'string', format: 'binary' } } },
  })
  async upload(@UploadedFile() file: Express.Multer.File, @Req() req: Request, @Res() res: Response) {
    try {
      const formData = new FormData();
      if (file) formData.append('file', file.buffer, file.originalname);

      const { data } = await firstValueFrom(
        this.httpService.post(`${this.fragApiUrl}/matches/upload`, formData, {
          headers: { ...formData.getHeaders(), ...this.getHeaders(req) },
        }),
      );
      res.status(202).json(data);
    } catch (error) {
      res.status(error.response?.status || 500).json(error.response?.data);
    }
  }
}