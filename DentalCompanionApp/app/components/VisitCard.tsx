import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export interface VisitCardProps {
  visit: {
    id: number;
    date: string;
    dent?: string | null;
    acte?: string | null;
    prix: number;
    paye: number;
    reste: number;
  };
}

export default function VisitCard({ visit }: VisitCardProps) {
  const formatDate = (dateString: string) => {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const formatCurrency = (amount: number) => `${amount?.toFixed(2) || '0.00'} MAD`;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.date}>{formatDate(visit.date)}</Text>
        {visit.dent ? <Text style={styles.tooth}>🦷 Tooth #{visit.dent}</Text> : null}
      </View>

      {visit.acte ? (
        <Text style={styles.acte}>{visit.acte}</Text>
      ) : null}

      <View style={styles.pricing}>
        <View style={styles.row}>
          <Text style={styles.label}>Total:</Text>
          <Text style={styles.value}>{formatCurrency(visit.prix)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Paid:</Text>
          <Text style={[styles.value, styles.paid]}>{formatCurrency(visit.paye)}</Text>
        </View>
        {visit.reste > 0 ? (
          <View style={styles.row}>
            <Text style={styles.label}>Remaining:</Text>
            <Text style={[styles.value, styles.remaining]}>{formatCurrency(visit.reste)}</Text>
          </View>
        ) : null}
      </View>
    </View>
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
    marginBottom: 10,
  },
  date: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  tooth: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '500',
  },
  acte: {
    fontSize: 15,
    color: '#555',
    marginBottom: 12,
    lineHeight: 20,
  },
  pricing: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  label: {
    fontSize: 14,
    color: '#666',
  },
  value: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  paid: {
    color: '#4CAF50',
  },
  remaining: {
    color: '#F44336',
  },
});
