using Microsoft.AspNetCore.Identity;
using NuIeee.Domain.Entities;

namespace NuIeee.Infrastructure.Identity;

public static class SeedIdentityData
{
    public static async Task SeedRolesAsync(RoleManager<IdentityRole<Guid>> roleManager)
    {
        string[] roleNames = ["SuperAdmin", "Admin", "Member"];

        foreach (var role in roleNames)
        {
            if (!await roleManager.RoleExistsAsync(role))
            {
                await roleManager.CreateAsync(new IdentityRole<Guid>(role));
            }
        }
    }

    public static async Task SeedSuperAdminAsync(UserManager<ApplicationUser> userManager)
    {
        var superAdmin = await userManager.FindByNameAsync("wstoccob");

        if (superAdmin != null && !await userManager.IsInRoleAsync(superAdmin, "SuperAdmin"))
        {
            await userManager.AddToRoleAsync(superAdmin, "SuperAdmin");
        }
    }
}