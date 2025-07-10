using MediatR;

namespace NuIeee.Application.Features.Users.Commands;

public record CreateUserCommand(string Username, string Fullname, string Password, string Role) : IRequest<Guid>;