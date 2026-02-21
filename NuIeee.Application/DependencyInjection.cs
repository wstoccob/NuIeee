using Microsoft.Extensions.DependencyInjection;
using NuIeee.Application.Services.Auth;
using NuIeee.Application.Services.Events;
using NuIeee.Application.Services.Hackathon;
using NuIeee.Application.Services.Users;

namespace NuIeee.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IJwtService, JwtService>();
        services.AddScoped<IAuthService, AuthService>();
        services.AddScoped<IEventService, EventService>();
        services.AddScoped<IHackathonService, HackathonService>();
        services.AddScoped<IUserService, UserService>();

        return services;
    }
}