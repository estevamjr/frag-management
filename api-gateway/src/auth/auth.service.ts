import { Injectable, UnauthorizedException, InternalServerErrorException, HttpException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';
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
      // 1. The Gateway forwards the login request to the Python backend
      const { data } = await firstValueFrom(
        this.httpService.post(`${this.backendUrl}/auth/login`, loginDto)
      );

      // 2. If Python validates, we create a JWT token here
      const payload = { 
        sub: data.id, 
        username: data.username,
        // Here we can add more user info if needed (roles, permissions, etc.)
      };

      return {
        access_token: this.jwtService.sign(payload),
        user: data
      };

    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 404) {
        throw new UnauthorizedException('User or password incorrect');
      }
      console.error('Error during login:', error.message);
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
}