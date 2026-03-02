import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import api from '../api/client';
import { Building2, Plus, Edit2, X, AlertCircle, CheckCircle, Trash2, Power, PowerOff, UserCog } from 'lucide-react';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  settings: Record<string, any>;
  is_active: boolean;
  created_at: string;
}

interface TenantForm {
  name: string;
  slug: string;
  is_active: boolean;
  // Admin fields (optional)
  admin_email?: string;
  admin_password?: string;
  admin_full_name?: string;
  create_with_admin?: boolean;
}

export default function Tenants() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [createWithAdmin, setCreateWithAdmin] = useState(true);
  const { register, handleSubmit, reset, setValue, formState: { isSubmitting, errors } } = useForm<TenantForm>({
    defaultValues: {
      create_with_admin: true,
    },
  });

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/tenants');
      setTenants(response.data);
    } catch (error: any) {
      console.error('Failed to fetch tenants:', error);
      setError(error.response?.data?.detail || 'Failed to fetch tenants');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: TenantForm) => {
    try {
      setError(null);
      setSuccess(null);
      
      console.log('Submitting tenant data:', data);
      
      if (editingTenant) {
        // Update existing tenant
        const response = await api.patch(`/tenants/${editingTenant.id}`, {
          name: data.name,
          is_active: data.is_active,
        });
        console.log('Update response:', response);
        setSuccess('Tenant updated successfully!');
      } else {
        // Create new tenant
        if (data.create_with_admin) {
          // Create tenant with admin
          const response = await api.post('/tenants/with-admin', {
            tenant: {
              name: data.name,
              slug: data.slug,
              is_active: data.is_active,
            },
            admin: {
              email: data.admin_email,
              password: data.admin_password,
              full_name: data.admin_full_name,
            },
          });
          console.log('Create with admin response:', response);
          setSuccess('Tenant and admin user created successfully!');
        } else {
          // Create tenant only
          const response = await api.post('/tenants', data);
          console.log('Create response:', response);
          setSuccess('Tenant created successfully!');
        }
      }
      
      reset();
      setShowCreateForm(false);
      setEditingTenant(null);
      
      // Wait a bit before refreshing to show success message
      setTimeout(() => {
        fetchTenants();
        setSuccess(null);
      }, 2000);
      
    } catch (error: any) {
      console.error('Failed to save tenant:', error);
      console.error('Error response:', error.response);
      setError(error.response?.data?.detail || 'Failed to save tenant. Please try again.');
    }
  };

  const handleEdit = (tenant: Tenant) => {
    setEditingTenant(tenant);
    setValue('name', tenant.name);
    setValue('slug', tenant.slug);
    setValue('is_active', tenant.is_active);
    setShowCreateForm(true);
  };

  const handleCancel = () => {
    setShowCreateForm(false);
    setEditingTenant(null);
    setCreateWithAdmin(true);
    reset();
  };

  const handleImpersonate = async (tenant: Tenant) => {
    try {
      setError(null);
      const response = await api.post(`/tenants/${tenant.id}/impersonate`);
      
      // Store the new token
      localStorage.setItem('token', response.data.access_token);
      
      // Show success message
      setSuccess(`Now accessing as: ${tenant.name}`);
      
      // Reload the page to apply new context
      setTimeout(() => {
        window.location.reload();
      }, 1500);
      
    } catch (error: any) {
      console.error('Failed to impersonate tenant:', error);
      setError(error.response?.data?.detail || 'Failed to switch tenant');
    }
  };

  const handleToggleActive = async (tenant: Tenant) => {
    const action = tenant.is_active ? 'deactivate' : 'activate';
    
    if (!confirm(`Are you sure you want to ${action} "${tenant.name}"?`)) {
      return;
    }

    try {
      setError(null);
      await api.patch(`/tenants/${tenant.id}/toggle-active`);
      setSuccess(`Tenant ${action}d successfully!`);
      
      setTimeout(() => {
        fetchTenants();
        setSuccess(null);
      }, 1500);
      
    } catch (error: any) {
      console.error('Failed to toggle tenant:', error);
      setError(error.response?.data?.detail || `Failed to ${action} tenant`);
    }
  };

  const handleDelete = async (tenant: Tenant) => {
    if (!confirm(
      `⚠️ WARNING: This will PERMANENTLY delete "${tenant.name}" and ALL its data!\n\n` +
      `This includes:\n` +
      `- All users\n` +
      `- All roles\n` +
      `- All projects\n` +
      `- All work items\n` +
      `- All audit logs\n\n` +
      `This action CANNOT be undone!\n\n` +
      `Type the tenant name to confirm: ${tenant.name}`
    )) {
      return;
    }

    const confirmation = prompt(`Type "${tenant.name}" to confirm deletion:`);
    
    if (confirmation !== tenant.name) {
      setError('Tenant name does not match. Deletion cancelled.');
      return;
    }

    try {
      setError(null);
      await api.delete(`/tenants/${tenant.id}`);
      setSuccess('Tenant permanently deleted!');
      
      setTimeout(() => {
        fetchTenants();
        setSuccess(null);
      }, 1500);
      
    } catch (error: any) {
      console.error('Failed to delete tenant:', error);
      setError(error.response?.data?.detail || 'Failed to delete tenant');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
          <p className="text-gray-600">Manage companies and organizations</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>New Tenant</span>
        </button>
      </div>

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <p className="text-green-800">{success}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <div className="flex-1">
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-700"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {editingTenant ? 'Edit Tenant' : 'Create New Tenant'}
            </h3>
            <button
              onClick={handleCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Company Name *
                </label>
                <input
                  {...register('name', { required: 'Company name is required' })}
                  className="input mt-1"
                  placeholder="Acme Corporation"
                />
                {errors.name && (
                  <p className="text-red-600 text-xs mt-1">{errors.name.message}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Slug (URL identifier) *
                </label>
                <input
                  {...register('slug', { 
                    required: 'Slug is required',
                    pattern: {
                      value: /^[a-z0-9-]+$/,
                      message: 'Only lowercase letters, numbers, and hyphens allowed'
                    }
                  })}
                  className="input mt-1"
                  placeholder="acme-corp"
                  disabled={!!editingTenant}
                />
                {errors.slug && (
                  <p className="text-red-600 text-xs mt-1">{errors.slug.message}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Lowercase, no spaces. Cannot be changed after creation.
                </p>
              </div>
            </div>
            
            {!editingTenant && (
              <>
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      {...register('create_with_admin')}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      checked={createWithAdmin}
                      onChange={(e) => setCreateWithAdmin(e.target.checked)}
                    />
                    <label className="ml-2 block text-sm font-medium text-gray-900">
                      Create admin user for this tenant
                    </label>
                  </div>

                  {createWithAdmin && (
                    <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900">Admin User Details</h4>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Admin Full Name *
                        </label>
                        <input
                          {...register('admin_full_name', { 
                            required: createWithAdmin ? 'Admin name is required' : false 
                          })}
                          className="input mt-1"
                          placeholder="John Doe"
                        />
                        {errors.admin_full_name && (
                          <p className="text-red-600 text-xs mt-1">{errors.admin_full_name.message}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Admin Email *
                        </label>
                        <input
                          type="email"
                          {...register('admin_email', { 
                            required: createWithAdmin ? 'Admin email is required' : false,
                            pattern: {
                              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                              message: 'Invalid email address'
                            }
                          })}
                          className="input mt-1"
                          placeholder="admin@company.com"
                        />
                        {errors.admin_email && (
                          <p className="text-red-600 text-xs mt-1">{errors.admin_email.message}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Admin Password *
                        </label>
                        <input
                          type="password"
                          {...register('admin_password', { 
                            required: createWithAdmin ? 'Admin password is required' : false,
                            minLength: {
                              value: 6,
                              message: 'Password must be at least 6 characters'
                            }
                          })}
                          className="input mt-1"
                          placeholder="••••••••"
                        />
                        {errors.admin_password && (
                          <p className="text-red-600 text-xs mt-1">{errors.admin_password.message}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Minimum 6 characters
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            <div className="flex items-center">
              <input
                type="checkbox"
                {...register('is_active')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                defaultChecked={true}
              />
              <label className="ml-2 block text-sm text-gray-900">
                Active
              </label>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary disabled:opacity-50"
              >
                {isSubmitting ? 'Saving...' : editingTenant ? 'Update Tenant' : 'Create Tenant'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tenants List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tenants.map((tenant) => (
          <div key={tenant.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start space-x-3 flex-1">
                <div className="p-2 bg-primary-50 rounded-lg">
                  <Building2 className="h-5 w-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900">{tenant.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Slug: {tenant.slug}
                  </p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        tenant.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {tenant.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleImpersonate(tenant)}
                  className="text-blue-600 hover:text-blue-700 p-2 rounded hover:bg-blue-50"
                  title="Access as this tenant"
                >
                  <UserCog className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleEdit(tenant)}
                  className="text-gray-600 hover:text-primary-600 p-2 rounded hover:bg-gray-100"
                  title="Edit tenant"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleToggleActive(tenant)}
                  className={`p-2 rounded hover:bg-gray-100 ${
                    tenant.is_active 
                      ? 'text-orange-600 hover:text-orange-700' 
                      : 'text-green-600 hover:text-green-700'
                  }`}
                  title={tenant.is_active ? 'Deactivate tenant' : 'Activate tenant'}
                >
                  {tenant.is_active ? (
                    <PowerOff className="h-4 w-4" />
                  ) : (
                    <Power className="h-4 w-4" />
                  )}
                </button>
                <button
                  onClick={() => handleDelete(tenant)}
                  className="text-red-600 hover:text-red-700 p-2 rounded hover:bg-red-50"
                  title="Delete tenant"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <p className="text-xs text-gray-400">
                {new Date(tenant.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      {tenants.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tenants</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new tenant.
          </p>
        </div>
      )}
    </div>
  );
}
