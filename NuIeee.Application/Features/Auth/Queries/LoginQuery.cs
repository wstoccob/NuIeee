using MediatR;
using NuIeee.Application.DTOs.Auth;

namespace NuIeee.Application.Features.Auth.Queries;

public class LoginQuery : IRequest<string>
{
    public LoginDto LoginDto { get; set; }

    public LoginQuery(LoginDto loginDto)
    {
        LoginDto = loginDto;
    }
}
