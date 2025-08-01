using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using NuIeee.Infrastructure.Identity;
using NuIeee.Infrastructure.Persistence;
using NuIeee.Infrastructure.Repositories;
using NuIeee.Infrastructure.Services.Jwt;

namespace NuIeee.Infrastructure.Extensions;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration config)
    {
        var connString = config["DefaultConnection"];
        services.AddDbContext<ApplicationDbContext>(options =>
            options.UseNpgsql(connString));

        services.AddIdentity<ApplicationUser, IdentityRole<Guid>>(options =>
            {
                options.User.RequireUniqueEmail = false;
            })
            .AddEntityFrameworkStores<ApplicationDbContext>()
            .AddDefaultTokenProviders();

        services.AddScoped<IHackathonRepository, HackathonRepository>();
        services.AddScoped<IUserManagementRepository, UserManagementRepository>();
        services.AddScoped<IJwtService, JwtService>();
        

        
        return services;
    }
}