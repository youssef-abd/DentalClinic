import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';

export interface PatientCardProps {
  patient: {
    id: number;
    nom: string;
    prenom: string;
    telephone?: string | null;
    date_naissance?: string | null;
    profession?: string | null;
    assurance?: string | null;
    created_at: string;
  };
  onPress: () => void;
}

export default function PatientCard({ patient, onPress }: PatientCardProps) {
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'N/A';
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.header}>
        <Text style={styles.name}>{patient.nom} {patient.prenom}</Text>
        <Text style={styles.created}>{formatDate(patient.created_at)}</Text>
      </View>
      <View style={styles.details}>
        <Text style={styles.info}>📞 {patient.telephone || 'N/A'}</Text>
        <Text style={styles.info}>🎂 {patient.date_naissance ? formatDate(patient.date_naissance) : 'N/A'}</Text>
      </View>
      {patient.profession ? (
        <Text style={styles.profession}>💼 {patient.profession}</Text>
      ) : null}
      {patient.assurance ? (
        <Text style={styles.insurance}>🏥 {patient.assurance}</Text>
      ) : null}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  created: {
    fontSize: 12,
    color: '#666',
  },
  details: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  info: {
    fontSize: 14,
    color: '#555',
    flex: 1,
  },
  profession: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  insurance: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
});
