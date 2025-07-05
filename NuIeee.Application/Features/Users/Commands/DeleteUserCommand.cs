using MediatR;

namespace NuIeee.Application.Features.Users.Commands;

public record DeleteUserCommand(Guid UserId) : IRequest;