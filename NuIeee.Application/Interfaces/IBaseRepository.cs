namespace NuIeee.Application.Interfaces;

public interface IBaseRepository<TEntity, TDto> where TEntity : class
{
    void  Add<TEntity>(TEntity entity) where TEntity : class;
}