import { NextResponse } from 'next/server';

/**
 * Health check endpoint for container orchestration
 * Returns 200 OK with basic status information
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'frontend',
    },
    { status: 200 }
  );
}
