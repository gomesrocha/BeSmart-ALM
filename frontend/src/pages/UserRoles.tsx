import { useEffect, useState } from 'react';
import api from '../api/client';
import { Users, Shield, Plus, X, Search } from 'lucide-react';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles?: Role[];
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions?: string[];
}

export default function UserRoles() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, rolesRes] = await Promise.all([
        api.get('/users'),
        api.get('/roles'),
      ]);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserRoles = async (userId: string) => {
    try {
      const response = await api.get(`/users/${userId}/roles`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user roles:', error);
      return [];
    }
  };

  const handleUserClick = async (user: User) => {
    const userRoles = await fetchUserRoles(user.id);
    setSelectedUser({ ...user, roles: userRoles });
  };

  const handleAssignRole = async (roleId: string) => {
    if (!selectedUser) return;

    try {
      await api.post(`/users/${selectedUser.id}/roles`, { role_id: roleId });
      // Refresh user roles
      const userRoles = await fetchUserRoles(selectedUser.id);
      setSelectedUser({ ...selectedUser, roles: userRoles });
      setShowAssignModal(false);
    } catch (error) {
      console.error('Failed to assign role:', error);
    }
  };

  const handleRemoveRole = async (roleId: string) => {
    if (!selectedUser) return;

    try {
      await api.delete(`/users/${selectedUser.id}/roles/${roleId}`);
      // Refresh user roles
      const userRoles = await fetchUserRoles(selectedUser.id);
      setSelectedUser({ ...selectedUser, roles: userRoles });
    } catch (error) {
      console.error('Failed to remove role:', error);
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const availableRoles = roles.filter(
    (role) => !selectedUser?.roles?.some((ur) => ur.id === role.id)
  );

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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Roles</h1>
        <p className="text-gray-600">Manage user roles and permissions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Users List */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Users</h3>

          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Users */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredUsers.map((user) => (
              <button
                key={user.id}
                onClick={() => handleUserClick(user)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  selectedUser?.id === user.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gray-100 rounded-full">
                    <Users className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">
                      {user.full_name}
                    </p>
                    <p className="text-sm text-gray-500 truncate">{user.email}</p>
                  </div>
                  {!user.is_active && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                      Inactive
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>

          {filteredUsers.length === 0 && (
            <div className="text-center py-8">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">No users found</p>
            </div>
          )}
        </div>

        {/* User Roles */}
        <div className="card">
          {selectedUser ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {selectedUser.full_name}
                  </h3>
                  <p className="text-sm text-gray-500">{selectedUser.email}</p>
                </div>
                <button
                  onClick={() => setShowAssignModal(true)}
                  className="btn btn-sm btn-primary flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Assign Role</span>
                </button>
              </div>

              {/* Current Roles */}
              <div className="space-y-2">
                {selectedUser.roles && selectedUser.roles.length > 0 ? (
                  selectedUser.roles.map((role) => (
                    <div
                      key={role.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <Shield className="h-5 w-5 text-primary-600" />
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{role.name}</p>
                          <p className="text-sm text-gray-500">{role.description}</p>
                          {role.permissions && role.permissions.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {role.permissions.slice(0, 3).map((perm) => (
                                <span
                                  key={perm}
                                  className="px-2 py-0.5 text-xs font-medium rounded bg-blue-100 text-blue-800"
                                >
                                  {perm}
                                </span>
                              ))}
                              {role.permissions.length > 3 && (
                                <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-600">
                                  +{role.permissions.length - 3} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveRole(role.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Shield className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-sm text-gray-500">No roles assigned</p>
                  </div>
                )}
              </div>

              {/* Assign Role Modal */}
              {showAssignModal && (
                <div 
                  className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                  onClick={() => setShowAssignModal(false)}
                >
                  <div 
                    className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        Assign Role
                      </h3>
                      <button
                        onClick={() => setShowAssignModal(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>

                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {availableRoles.length > 0 ? (
                        availableRoles.map((role) => (
                          <button
                            key={role.id}
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              handleAssignRole(role.id);
                            }}
                            className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer"
                          >
                            <div className="flex items-center space-x-3">
                              <Shield className="h-5 w-5 text-primary-600" />
                              <div className="flex-1">
                                <p className="font-medium text-gray-900">{role.name}</p>
                                <p className="text-sm text-gray-500">
                                  {role.description}
                                </p>
                                {role.permissions && role.permissions.length > 0 && (
                                  <div className="mt-2 flex flex-wrap gap-1">
                                    {role.permissions.map((perm) => (
                                      <span
                                        key={perm}
                                        className="px-2 py-0.5 text-xs font-medium rounded bg-blue-100 text-blue-800"
                                      >
                                        {perm}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </button>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <Shield className="mx-auto h-12 w-12 text-gray-400" />
                          <p className="mt-2 text-sm text-gray-500">
                            All roles already assigned
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">
                Select a user to manage their roles
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
