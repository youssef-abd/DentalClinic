import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
  StatusBar,
  RefreshControl,
  Switch,
} from 'react-native';
import PatientCard from './components/PatientCard';
import VisitCard from './components/VisitCard';
import { supabase } from './lib/supabase';
import * as Haptics from 'expo-haptics';

interface Patient {
  id: number;
  nom: string;
  prenom: string;
  date_naissance: string | null;
  telephone: string | null;
  numero_carte_national?: string | null;
  assurance: string | null;
  profession: string | null;
  maladie?: string | null;
  observation?: string | null;
  xray_photo?: string | null;
  created_at: string;
}

interface Visit {
  id: number;
  date: string;
  dent?: string | null;
  acte?: string | null;
  prix: number;
  paye: number;
  reste: number;
  patient_id: number;
}

interface User {
  id: string;
  email: string;
}

const DentalCompanionApp = () => {
  // Authentication state
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  
  // App state
  const [currentView, setCurrentView] = useState<'patients' | 'visits'>('patients');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [visitsLoading, setVisitsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [recentOnly, setRecentOnly] = useState(false);
  const pageSize = 20;
  
  // Cache for better performance
  const [visitsCache, setVisitsCache] = useState<Record<number, Visit[]>>({});

  // Check if user is already logged in
  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ? {
        id: session.user.id,
        email: session.user.email || ''
      } : null);
      if (session?.user) {
        fetchPatients();
      }
    } catch (error) {
      console.error('Error checking user:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle login
  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }
    const emailOk = /.+@.+\..+/.test(email.trim());
    if (!emailOk) {
      setLoginError('Enter a valid email address');
      return;
    }

    setLoginLoading(true);
    setLoginError(null);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (error) {
        setLoginError(error.message || 'Invalid email or password');
      } else if (data?.user) {
        setUser({ id: data.user.id, email: data.user.email || '' });
        await fetchPatients(true);
      } else {
        setLoginError('Login failed. Please try again.');
      }
    } catch (error) {
      setLoginError('Unexpected error. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      setUser(null);
      setPatients([]);
      setFilteredPatients([]);
      setVisits([]);
      setSelectedPatient(null);
      setCurrentView('patients');
            setVisitsCache({});
      setEmail('');
      setPassword('');
    } catch (error) {
      Alert.alert('Error', 'Failed to logout');
    }
  };

  // Fetch patients from Supabase
  const fetchPatients = async (reset = false) => {
    if (reset) {
      setPage(0);
      setHasMore(true);
    }

    const currentPage = reset ? 0 : page;
    if (reset) {
      setPatientsLoading(true);
    } else {
      setLoadingMore(true);
    }
    setErrorMsg(null);

    try {
      let query = supabase
        .from('patients')
        .select('id, nom, prenom, telephone, date_naissance, profession, assurance, created_at')
        .order('created_at', { ascending: false });

      const q = searchQuery.trim();
      if (q) {
        query = query.or(
          `nom.ilike.%${q}%,prenom.ilike.%${q}%,telephone.ilike.%${q}%`
        );
      }
      if (recentOnly) {
        const d = new Date();
        d.setDate(d.getDate() - 30);
        query = query.gte('created_at', d.toISOString());
      }

      const from = currentPage * pageSize;
      const to = from + pageSize - 1;

      const { data, error } = await query.range(from, to);

      if (error) throw error;

      const batch = data || [];
      if (reset) {
        setPatients(batch);
        setFilteredPatients(batch);
      } else {
        setPatients(prev => [...prev, ...batch]);
        setFilteredPatients(prev => [...prev, ...batch]);
      }

      const more = batch.length === pageSize;
      setHasMore(more);
      setPage(currentPage + (more ? 1 : 0));
    } catch (error: any) {
      setErrorMsg('Failed to load patient data. Pull to retry.');
    } finally {
      setPatientsLoading(false);
      setLoadingMore(false);
    }
  };

  // Fetch visits for a specific patient
  const fetchVisits = async (patientId: number, useCache = true) => {
    if (useCache && visitsCache[patientId]) {
      setVisits(visitsCache[patientId]);
      return;
    }

    setVisitsLoading(true);
    setErrorMsg(null);
    try {
      const { data, error } = await supabase
        .from('visits')
        .select('id, date, dent, acte, prix, paye, reste, patient_id')
        .eq('patient_id', patientId)
        .order('date', { ascending: false });

      if (error) throw error;

      const visitsData = data || [];
      setVisits(visitsData);
      setVisitsCache(prev => ({
        ...prev,
        [patientId]: visitsData
      }));
    } catch (error: any) {
      setErrorMsg('Failed to load visit history. Pull to retry.');
    } finally {
      setVisitsLoading(false);
    }
  };

  // Handle search
  // Debounced search -> server-side
  useEffect(() => {
    const id = setTimeout(() => {
      fetchPatients(true);
    }, 300);
    return () => clearTimeout(id);
  }, [searchQuery]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // Handle patient selection
  const selectPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    setCurrentView('visits');
    fetchVisits(patient.id);
  };

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try { await Haptics.selectionAsync(); } catch {}
    if (currentView === 'patients') {
      await fetchPatients(true);
    } else if (selectedPatient) {
      await fetchVisits(selectedPatient.id, false);
    }
    setRefreshing(false);
  };

  
  // Render patient item
  const renderPatientItem = ({ item }: { item: Patient }) => (
    <PatientCard patient={item} onPress={() => selectPatient(item)} />
  );

  // Render visit item
  const renderVisitItem = ({ item }: { item: Visit }) => (
    <VisitCard visit={item} />
  );

  // Loading screen
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // Login screen
  if (!user) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
        <View style={styles.loginContainer}>
          <Text style={styles.title}>🦷 Dental Companion</Text>
          <Text style={styles.subtitle}>Mobile App for Dentists</Text>
          
          <View style={styles.loginForm}>
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor="#d0d0d0"
              underlineColorAndroid="transparent"
              value={email}
              onChangeText={(t) => { setEmail(t); setLoginError(null); }}
              autoCapitalize="none"
              editable={!loginLoading}
            />
            
            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor="#d0d0d0"
              underlineColorAndroid="transparent"
              value={password}
              onChangeText={(t) => { setPassword(t); setLoginError(null); }}
              secureTextEntry
              editable={!loginLoading}
            />
            
            <TouchableOpacity
              style={[styles.loginButton, loginLoading && styles.disabledButton]}
              onPress={handleLogin}
              disabled={loginLoading}
            >
              {loginLoading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.loginButtonText}>Login</Text>
              )}
            </TouchableOpacity>
            {loginError ? (
              <Text style={[styles.errorText, { marginTop: 10 }]}>{loginError}</Text>
            ) : null}
          </View>
        </View>
      </View>
    );
  }

  // Main app screens
  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2196F3" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          {currentView === 'visits' ? (
            <TouchableOpacity
              onPress={() => {
                setCurrentView('patients');
                setSelectedPatient(null);
                setVisits([]);
              }}
            >
              <Text style={styles.backButton}>← Back</Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.headerTitle}>🦷 Patients</Text>
          )}
          
          <TouchableOpacity onPress={handleLogout}>
            <Text style={styles.logoutButton}>Logout</Text>
          </TouchableOpacity>
        </View>
        
        {currentView === 'visits' && selectedPatient && (
          <Text style={styles.patientTitle}>
            {selectedPatient.nom} {selectedPatient.prenom}
          </Text>
        )}
      </View>

      {/* Content */}
      {currentView === 'patients' ? (
        <View style={styles.content}>
          {/* Search Bar */}
          <View style={styles.searchRow}>
            <TextInput
              style={[styles.searchInput, { flex: 1 }]}
              placeholder="Search patients by name or phone..."
              value={searchQuery}
              onChangeText={handleSearch}
            />
            {!!searchQuery && (
              <TouchableOpacity
                accessibilityRole="button"
                accessibilityLabel="Clear search"
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                onPress={() => setSearchQuery('')}
                style={styles.clearBtn}
              >
                <Text style={styles.clearBtnText}>✕</Text>
              </TouchableOpacity>
            )}
          </View>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Recent (last 30 days)</Text>
            <Switch
              value={recentOnly}
              onValueChange={(v) => { setRecentOnly(v); fetchPatients(true); }}
            />
          </View>
          
          {/* Patients List */}
          {errorMsg && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>{errorMsg}</Text>
              <TouchableOpacity
                accessibilityRole="button"
                accessibilityLabel="Retry"
                onPress={() => fetchPatients(true)}
                style={styles.retryBtn}
              >
                <Text style={styles.retryText}>Retry</Text>
              </TouchableOpacity>
            </View>
          )}

          {patientsLoading ? (
            <View style={styles.listContainer}>
              {Array.from({ length: 6 }).map((_, i) => (
                <View key={i} style={styles.skelCard}>
                  <View style={[styles.skelBar, { width: '60%' }]} />
                  <View style={[styles.skelBar, { width: '40%' }]} />
                  <View style={[styles.skelBar, { width: '80%' }]} />
                </View>
              ))}
            </View>
          ) : (
            <FlatList
              data={filteredPatients}
              renderItem={renderPatientItem}
              keyExtractor={(item) => item.id.toString()}
              contentContainerStyle={styles.listContainer}
              refreshControl={
                <RefreshControl
                  refreshing={refreshing}
                  onRefresh={handleRefresh}
                  colors={['#2196F3']}
                />
              }
              ListEmptyComponent={
                <View style={styles.emptyContainer}>
                  <Text style={styles.emptyText}>
                    {searchQuery ? 'No patients found matching your search' : 'No patients found'}
                  </Text>
                </View>
              }
              initialNumToRender={12}
              maxToRenderPerBatch={24}
              windowSize={7}
              removeClippedSubviews
              getItemLayout={(data, index) => ({ length: 92, offset: 92 * index, index })}
              onEndReachedThreshold={0.5}
              onEndReached={() => {
                if (!patientsLoading && !loadingMore && hasMore) {
                  fetchPatients(false);
                }
              }}
            />
          )}
        </View>
      ) : (
        <View style={styles.content}>
          {/* Visits List */}
          {errorMsg && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>{errorMsg}</Text>
              <TouchableOpacity
                accessibilityRole="button"
                accessibilityLabel="Retry"
                onPress={() => selectedPatient ? fetchVisits(selectedPatient.id, false) : null}
                style={styles.retryBtn}
              >
                <Text style={styles.retryText}>Retry</Text>
              </TouchableOpacity>
            </View>
          )}

          {visitsLoading ? (
            <View style={styles.listContainer}>
              {Array.from({ length: 4 }).map((_, i) => (
                <View key={i} style={styles.skelCard}>
                  <View style={[styles.skelBar, { width: '50%' }]} />
                  <View style={[styles.skelBar, { width: '30%' }]} />
                  <View style={[styles.skelBar, { width: '70%' }]} />
                </View>
              ))}
            </View>
          ) : (
            <FlatList
              data={visits}
              renderItem={renderVisitItem}
              keyExtractor={(item) => item.id.toString()}
              contentContainerStyle={styles.listContainer}
              refreshControl={
                <RefreshControl
                  refreshing={refreshing}
                  onRefresh={handleRefresh}
                  colors={['#2196F3']}
                />
              }
              ListEmptyComponent={
                <View style={styles.emptyContainer}>
                  <Text style={styles.emptyText}>No visits found for this patient</Text>
                </View>
              }
              initialNumToRender={10}
              maxToRenderPerBatch={20}
              windowSize={6}
              removeClippedSubviews
              getItemLayout={(data, index) => ({ length: 120, offset: 120 * index, index })}
            />
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  
  // Login Styles
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
    textAlign: 'center',
  },
  loginForm: {
    width: '100%',
    maxWidth: 300,
  },
  input: {
    backgroundColor: 'transparent',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 0,
    borderColor: 'transparent',
  },
  loginButton: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  disabledButton: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  
  // Header Styles
  header: {
    backgroundColor: '#2196F3',
    paddingTop: 40,
    paddingBottom: 15,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  backButton: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  logoutButton: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  patientTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 8,
  },
  
  // Content Styles
  content: {
    flex: 1,
  },
  searchInput: {
    backgroundColor: 'white',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  listContainer: {
    paddingHorizontal: 15,
    paddingBottom: 20,
  },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 15,
  },
  clearBtn: {
    marginLeft: 8,
    backgroundColor: '#eee',
    borderRadius: 16,
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  clearBtnText: {
    fontSize: 16,
    color: '#666',
  },
  filterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginHorizontal: 15,
    marginTop: 8,
  },
  filterLabel: {
    fontSize: 14,
    color: '#666',
  },
  
  // Removed inline card styles (moved to components)
  
  // Empty State
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  errorBanner: {
    backgroundColor: '#ffefef',
    borderColor: '#f5c6cb',
    borderWidth: 1,
    padding: 10,
    marginHorizontal: 15,
    marginTop: 10,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: {
    color: '#a94442',
    fontSize: 14,
  },
  retryBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f5c6cb',
    borderRadius: 6,
  },
  retryText: {
    color: '#7a1c1c',
    fontWeight: '600',
  },
  skelCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  skelBar: {
    height: 12,
    backgroundColor: '#eee',
    borderRadius: 8,
    marginBottom: 8,
  },
});

export default DentalCompanionApp;