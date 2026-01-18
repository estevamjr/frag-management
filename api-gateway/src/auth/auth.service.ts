import { Injectable, UnauthorizedException, InternalServerErrorException, HttpException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';
import { URLSearchParams } from 'url';

import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';

@Injectable()
export class AuthService {
  private backendUrl: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {
    this.backendUrl = this.configService.get<string>('BACKEND_URL') ?? '';
  }

  async login(loginDto: LoginDto) {
    try {
      const params = new URLSearchParams();
      params.append('username', loginDto.username);
      params.append('password', loginDto.password);

      console.log(`📡 Sendind request for login to: ${this.backendUrl}/auth/token`);

      const { data } = await firstValueFrom(
        this.httpService.post(`${this.backendUrl}/auth/token`, params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
      );

      return data;

    } catch (error) {
      console.error('❌ Erro no login (Gateway):', error.response?.data || error.message);
      
      if (error.response?.status === 401 || error.response?.status === 404 || error.response?.status === 422) {
        throw new UnauthorizedException('User or password incorrect');
      }
      throw new InternalServerErrorException('Internal server error during login');
    }
  }

  async register(registerDto: RegisterDto) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.post(`${this.backendUrl}/auth/register`, registerDto)
      );
      return data;
    } catch (error: any) {
      throw new HttpException(
        error.response?.data || 'Error connecting to backend service',
        error.response?.status || 500,
      );
    }
  }

  async getMe(token: string) {
    try {
      const { data } = await firstValueFrom(
        this.httpService.get(`${this.backendUrl}/auth/me`, {
          headers: { Authorization: token }, 
        })
      );
      return data;
    } catch (error) {
      throw new HttpException(
        error.response?.data || 'Erro ao buscar perfil',
        error.response?.status || 500,
      );
    }
  }
}