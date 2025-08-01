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
} from 'react-native';
import { createClient } from '@supabase/supabase-js';

// Use environment variables instead of hardcoded values
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

interface Patient {
  id: number;
  nom: string;
  prenom: string;
  date_naissance: string;
  telephone: string;
  numero_carte_national: string;
  assurance: string;
  profession: string;
  maladie: string;
  observation: string;
  xray_photo: string;
  created_at: string;
}

interface Visit {
  id: number;
  date: string;
  dent: string;
  acte: string;
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
  const [email, setEmail] = useState('dentist@test.com');
  const [password, setPassword] = useState('password123');
  const [loginLoading, setLoginLoading] = useState(false);
  
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
  
  // Cache for better performance
  const [patientsCache, setPatientsCache] = useState<Patient[] | null>(null);
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

    setLoginLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password: password,
      });

      if (error) {
        Alert.alert('Login Error', error.message);
      } else {
        setUser(data.user ? {
          id: data.user.id,
          email: data.user.email || ''
        } : null);
        fetchPatients();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to connect. Please check your internet connection.');
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
      setPatientsCache(null);
      setVisitsCache({});
    } catch (error) {
      Alert.alert('Error', 'Failed to logout');
    }
  };

  // Fetch patients from Supabase
  const fetchPatients = async (useCache = true) => {
    if (useCache && patientsCache) {
      setPatients(patientsCache);
      setFilteredPatients(patientsCache);
      return;
    }

    setPatientsLoading(true);
    try {
      const { data, error } = await supabase
        .from('patients')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        throw error;
      }

      const patientsData = data || [];
      setPatients(patientsData);
      setFilteredPatients(patientsData);
      setPatientsCache(patientsData);
    } catch (error) {
      Alert.alert(
        'Error Loading Patients',
        'Failed to load patient data. Please check your connection and try again.',
        [
          { text: 'Retry', onPress: () => fetchPatients(false) },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    } finally {
      setPatientsLoading(false);
    }
  };

  // Fetch visits for a specific patient
  const fetchVisits = async (patientId: number, useCache = true) => {
    if (useCache && visitsCache[patientId]) {
      setVisits(visitsCache[patientId]);
      return;
    }

    setVisitsLoading(true);
    try {
      const { data, error } = await supabase
        .from('visits')
        .select('*')
        .eq('patient_id', patientId)
        .order('date', { ascending: false });

      if (error) {
        throw error;
      }

      const visitsData = data || [];
      setVisits(visitsData);
      setVisitsCache(prev => ({
        ...prev,
        [patientId]: visitsData
      }));
    } catch (error) {
      Alert.alert(
        'Error Loading Visits',
        'Failed to load visit history. Please try again.',
        [
          { text: 'Retry', onPress: () => fetchVisits(patientId, false) },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    } finally {
      setVisitsLoading(false);
    }
  };

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setFilteredPatients(patients);
      return;
    }

    const filtered = patients.filter(patient => {
      const fullName = `${patient.nom} ${patient.prenom}`.toLowerCase();
      return fullName.includes(query.toLowerCase());
    });
    setFilteredPatients(filtered);
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
    if (currentView === 'patients') {
      await fetchPatients(false);
    } else if (selectedPatient) {
      await fetchVisits(selectedPatient.id, false);
    }
    setRefreshing(false);
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return `${amount?.toFixed(2) || '0.00'} MAD`;
  };

  // Render patient item
  const renderPatientItem = ({ item }: { item: Patient }) => (
    <TouchableOpacity
      style={styles.patientCard}
      onPress={() => selectPatient(item)}
    >
      <View style={styles.patientHeader}>
        <Text style={styles.patientName}>
          {item.nom} {item.prenom}
        </Text>
        <Text style={styles.patientDate}>
          {formatDate(item.created_at)}
        </Text>
      </View>
      <View style={styles.patientDetails}>
        <Text style={styles.patientInfo}>
          📞 {item.telephone || 'N/A'}
        </Text>
        <Text style={styles.patientInfo}>
          🎂 {item.date_naissance ? formatDate(item.date_naissance) : 'N/A'}
        </Text>
      </View>
      {item.profession && (
        <Text style={styles.patientProfession}>
          💼 {item.profession}
        </Text>
      )}
      {item.assurance && (
        <Text style={styles.patientInsurance}>
          🏥 {item.assurance}
        </Text>
      )}
    </TouchableOpacity>
  );

  // Render visit item
  const renderVisitItem = ({ item }: { item: Visit }) => (
    <View style={styles.visitCard}>
      <View style={styles.visitHeader}>
        <Text style={styles.visitDate}>
          {formatDate(item.date)}
        </Text>
        {item.dent && (
          <Text style={styles.toothNumber}>
            🦷 Tooth #{item.dent}
          </Text>
        )}
      </View>
      
      {item.acte && (
        <Text style={styles.treatmentDescription}>
          {item.acte}
        </Text>
      )}
      
      <View style={styles.visitPricing}>
        <View style={styles.priceRow}>
          <Text style={styles.priceLabel}>Total:</Text>
          <Text style={styles.priceValue}>
            {formatCurrency(item.prix)}
          </Text>
        </View>
        
        <View style={styles.priceRow}>
          <Text style={styles.priceLabel}>Paid:</Text>
          <Text style={[styles.priceValue, styles.paidAmount]}>
            {formatCurrency(item.paye)}
          </Text>
        </View>
        
        {item.reste > 0 && (
          <View style={styles.priceRow}>
            <Text style={styles.priceLabel}>Remaining:</Text>
            <Text style={[styles.priceValue, styles.remainingAmount]}>
              {formatCurrency(item.reste)}
            </Text>
          </View>
        )}
      </View>
    </View>
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
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              editable={!loginLoading}
            />
            
            <TextInput
              style={styles.input}
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
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
          <TextInput
            style={styles.searchInput}
            placeholder="Search patients by name..."
            value={searchQuery}
            onChangeText={handleSearch}
          />
          
          {/* Patients List */}
          {patientsLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#2196F3" />
              <Text style={styles.loadingText}>Loading patients...</Text>
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
            />
          )}
        </View>
      ) : (
        <View style={styles.content}>
          {/* Visits List */}
          {visitsLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#2196F3" />
              <Text style={styles.loadingText}>Loading visits...</Text>
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
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
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
  
  // Patient Card Styles
  patientCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  patientHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  patientName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  patientDate: {
    fontSize: 12,
    color: '#666',
  },
  patientDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  patientInfo: {
    fontSize: 14,
    color: '#555',
    flex: 1,
  },
  patientProfession: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  patientInsurance: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  
  // Visit Card Styles
  visitCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  visitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  visitDate: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  toothNumber: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '500',
  },
  treatmentDescription: {
    fontSize: 15,
    color: '#555',
    marginBottom: 12,
    lineHeight: 20,
  },
  visitPricing: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  priceLabel: {
    fontSize: 14,
    color: '#666',
  },
  priceValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  paidAmount: {
    color: '#4CAF50',
  },
  remainingAmount: {
    color: '#F44336',
  },
  
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
});

export default DentalCompanionApp;